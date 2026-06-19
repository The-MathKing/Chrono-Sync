import re

with open('index.html', 'r') as f:
    html = f.read()

# 1. Add globalTick
if 'let globalTick = 0;' not in html:
    html = html.replace('let cameraFlash = 0;', 'let cameraFlash = 0;\nlet globalTick = 0;')

# 2. Add arrays for new mechanics
if 'let conveyorsRightPast =' not in html:
    html = html.replace('let jumpPadsPast = []; let jumpPadsFuture = [];', 
                        'let jumpPadsPast = []; let jumpPadsFuture = [];\nlet conveyorsRightPast = []; let conveyorsRightFuture = [];\nlet conveyorsLeftPast = []; let conveyorsLeftFuture = [];\nlet phasingPast = []; let phasingFuture = [];')

# 3. Add to loadLevel parser
parser_target = "if (char === 'C') crumblesPast.push(new CrumblingBlock(px, py));"
parser_repl = """if (char === 'C') crumblesPast.push(new CrumblingBlock(px, py));
            if (char === '+') conveyorsRightPast.push(new Rect(px, py + TILE_SIZE*0.8, TILE_SIZE, TILE_SIZE*0.2));
            if (char === '-') conveyorsLeftPast.push(new Rect(px, py + TILE_SIZE*0.8, TILE_SIZE, TILE_SIZE*0.2));
            if (char === 'V') phasingPast.push(new Rect(px, py, TILE_SIZE, TILE_SIZE));"""
html = html.replace(parser_target, parser_repl)

parser_f_target = "if (char === 'c') crumblesFuture.push(new CrumblingBlock(px, py));"
parser_f_repl = """if (char === 'c') crumblesFuture.push(new CrumblingBlock(px, py));
            if (char === '+') conveyorsRightFuture.push(new Rect(px, py + TILE_SIZE*0.8, TILE_SIZE, TILE_SIZE*0.2));
            if (char === '-') conveyorsLeftFuture.push(new Rect(px, py + TILE_SIZE*0.8, TILE_SIZE, TILE_SIZE*0.2));
            if (char === 'v') phasingFuture.push(new Rect(px, py, TILE_SIZE, TILE_SIZE));"""
html = html.replace(parser_f_target, parser_f_repl)

reset_target = "jumpPadsPast = []; jumpPadsFuture = []; crumblesPast = []; crumblesFuture = [];"
reset_repl = "jumpPadsPast = []; jumpPadsFuture = []; crumblesPast = []; crumblesFuture = [];\n    conveyorsRightPast = []; conveyorsRightFuture = []; conveyorsLeftPast = []; conveyorsLeftFuture = []; phasingPast = []; phasingFuture = [];"
html = html.replace(reset_target, reset_repl)

# 4. Update checkCollisions signature and logic
html = html.replace('checkCollisions(walls, blocks, crumbles, isX)', 'checkCollisions(walls, blocks, crumbles, phases, isX)')
html = html.replace('this.checkCollisions(walls, blocks, crumbles, true);', 'this.checkCollisions(walls, blocks, crumbles, phases, true);')
html = html.replace('this.checkCollisions(walls, blocks, crumbles, false);', 'this.checkCollisions(walls, blocks, crumbles, phases, false);')
html = html.replace('update(walls, blocks, pads, crumbles)', 'update(walls, blocks, pads, crumbles, phases, cR, cL)')

coll_logic_target = "for(let c of crumbles) if(c.active) collidables.push(c);"
coll_logic_repl = """for(let c of crumbles) if(c.active) collidables.push(c);
        if((globalTick % 240) < 120) {
            for(let p of phases) collidables.push(p);
        }"""
html = html.replace(coll_logic_target, coll_logic_repl)

# 5. Conveyor logic in Player.update
push_target = "this.x += this.vx;"
push_repl = """let pushX = 0;
        if(this.grounded) {
            for(let c of cR) if(this.x < c.x+c.w && this.x+this.w > c.x && this.y+this.h >= c.y && this.y+this.h <= c.y+2) pushX = 3;
            for(let c of cL) if(this.x < c.x+c.w && this.x+this.w > c.x && this.y+this.h >= c.y && this.y+this.h <= c.y+2) pushX = -3;
        }
        this.x += this.vx + pushX;"""
html = html.replace(push_target, push_repl)

# 6. Global tick update and pass new arrays
if 'globalTick++;' not in html:
    html = html.replace('function update() {\n    if (gameState !== \'playing\') return;', 'function update() {\n    if (gameState !== \'playing\') return;\n    globalTick++;')

html = html.replace('if(players[0]) players[0].update(staticPast, blocks, jumpPadsPast, crumblesPast);', 'if(players[0]) players[0].update(staticPast, blocks, jumpPadsPast, crumblesPast, phasingPast, conveyorsRightPast, conveyorsLeftPast);')
html = html.replace('if(players[1]) players[1].update(staticFuture, blocks, jumpPadsFuture, crumblesFuture);', 'if(players[1]) players[1].update(staticFuture, blocks, jumpPadsFuture, crumblesFuture, phasingFuture, conveyorsRightFuture, conveyorsLeftFuture);')

# 7. Rendering Phasing & Conveyors
render_tiles_target = "else if(char === 'C' || char === 'c') { ctx.fillStyle='#b85'; ctx.fillRect(px, py, TILE_SIZE, TILE_SIZE); ctx.strokeStyle='#421'; ctx.strokeRect(px, py, TILE_SIZE, TILE_SIZE); }"
render_tiles_repl = """else if(char === 'C' || char === 'c') { ctx.fillStyle='#b85'; ctx.fillRect(px, py, TILE_SIZE, TILE_SIZE); ctx.strokeStyle='#421'; ctx.strokeRect(px, py, TILE_SIZE, TILE_SIZE); }
            else if(char === '+') { ctx.fillStyle='#333'; ctx.fillRect(px, py+TILE_SIZE*0.8, TILE_SIZE, TILE_SIZE*0.2); ctx.fillStyle='#0ff'; ctx.fillRect(px+TILE_SIZE/2, py+TILE_SIZE*0.8, 4, 4); }
            else if(char === '-') { ctx.fillStyle='#333'; ctx.fillRect(px, py+TILE_SIZE*0.8, TILE_SIZE, TILE_SIZE*0.2); ctx.fillStyle='#0ff'; ctx.fillRect(px+TILE_SIZE/2, py+TILE_SIZE*0.8, 4, 4); }
            else if(char === 'V') { ctx.fillStyle='rgba(150,0,255,1)'; ctx.fillRect(px, py, TILE_SIZE, TILE_SIZE); }
            else if(char === 'v') { ctx.fillStyle='rgba(255,100,0,1)'; ctx.fillRect(px, py, TILE_SIZE, TILE_SIZE); }"""
html = html.replace(render_tiles_target, render_tiles_repl)

# 8. Render in actual game (Past)
past_draw_target = "if(players[0]) players[0].draw(ctx);"
past_draw_repl = """
        let phaseActive = (globalTick % 240) < 120;
        let phaseA = phaseActive ? 1.0 : 0.2;
        ctx.fillStyle = `rgba(150,0,255,${phaseA})`;
        for(let p of phasingPast) { ctx.fillRect(p.x, p.y, p.w, p.h); ctx.strokeStyle = `rgba(255,255,255,${phaseA})`; ctx.strokeRect(p.x+2, p.y+2, p.w-4, p.h-4); }
        
        ctx.fillStyle = '#333';
        for(let c of conveyorsRightPast) { ctx.fillRect(c.x, c.y, c.w, c.h); ctx.fillStyle='#0ff'; ctx.fillRect(c.x + (globalTick%40), c.y+2, 4, 4); }
        for(let c of conveyorsLeftPast) { ctx.fillStyle='#333'; ctx.fillRect(c.x, c.y, c.w, c.h); ctx.fillStyle='#0ff'; ctx.fillRect(c.x + (40 - (globalTick%40)), c.y+2, 4, 4); }

        if(players[0]) players[0].draw(ctx);"""
html = html.replace(past_draw_target, past_draw_repl)

future_draw_target = "if(players[1]) players[1].draw(ctx);"
future_draw_repl = """
        let phaseA2 = phaseActive ? 1.0 : 0.2;
        ctx.fillStyle = `rgba(255,100,0,${phaseA2})`;
        for(let p of phasingFuture) { ctx.fillRect(p.x, p.y, p.w, p.h); ctx.strokeStyle = `rgba(255,255,255,${phaseA2})`; ctx.strokeRect(p.x+2, p.y+2, p.w-4, p.h-4); }
        
        for(let c of conveyorsRightFuture) { ctx.fillStyle='#333'; ctx.fillRect(c.x, c.y, c.w, c.h); ctx.fillStyle='#f05'; ctx.fillRect(c.x + (globalTick%40), c.y+2, 4, 4); }
        for(let c of conveyorsLeftFuture) { ctx.fillStyle='#333'; ctx.fillRect(c.x, c.y, c.w, c.h); ctx.fillStyle='#f05'; ctx.fillRect(c.x + (40 - (globalTick%40)), c.y+2, 4, 4); }

        if(players[1]) players[1].draw(ctx);"""
html = html.replace(future_draw_target, future_draw_repl)


# 9. Update generateLevels with 20 levels
gen_target = re.compile(r'function generateLevels\(\) \{.*?\n\}\ngenerateLevels\(\);', re.DOTALL)

levels_code = """function generateLevels() {
    const L_W = "SSSSSSSSSSSSSSSS";
    const L_0 = "S..............S";
    function blank() {
        let arr = [];
        for(let i=0; i<18; i++) arr.push(i===0||i===17 ? L_W : L_0);
        return arr;
    }

    LVL_TEMPLATES.length = 0; // Clear initial 3

    // 1. Intro
    let l1P = blank(), l1F = blank();
    l1P[16] = "S..1........E..S"; l1F[16] = "S..2........e..S";
    LVL_TEMPLATES.push({ msg: "WASD / ARROWS to move.", hint: "Move to the portals.", story: "Two echoes separated by time.\\nOne pristine, the other ruined.\\nThey must align.", past: l1P, future: l1F });

    // 2. Jump
    let l2P = blank(), l2F = blank();
    l2P[16] = "S..1...WW...E..S"; l2F[16] = "S..2...ww...e..S";
    LVL_TEMPLATES.push({ msg: "Obstacles block the path.", hint: "Press W or UP.", past: l2P, future: l2F });

    // 3. Hazards
    let l3P = blank(), l3F = blank();
    l3P[16] = "S..1...LL...E..S"; l3F[16] = "S..2...TT...e..S";
    LVL_TEMPLATES.push({ msg: "Avoid red hazards.", hint: "Lasers and Thorns kill you.", past: l3P, future: l3F });

    // 4. Buttons
    let l4P = blank(), l4F = blank();
    l4P[16] = "S..1...>....E..S"; l4F[16] = "S..2...<....e..S";
    LVL_TEMPLATES.push({ msg: "Buttons open doors in the future.", hint: "Step on yellow buttons.", past: l4P, future: l4F });

    // 5. Push Blocks
    let l5P = blank(), l5F = blank();
    l5P[16] = "S..1..B.>...E..S"; l5F[16] = "S..2...<.......S";
    l5F[15] = "S......<....e..S";
    LVL_TEMPLATES.push({ msg: "Push blocks onto buttons.", hint: "Walk into grey blocks.", past: l5P, future: l5F });

    // 6. Jump Pads
    let l6P = blank(), l6F = blank();
    l6P[16] = "S..1..J........S"; l6F[16] = "S..2..j........S";
    l6P[10] = "S...........E..S"; l6F[10] = "S...........e..S";
    LVL_TEMPLATES.push({ msg: "Jump Pads boost height.", hint: "Green pads launch you.", story: "Some technologies outlasted the ages.\\nOthers merely crumbled under weight.", past: l6P, future: l6F });

    // 7. Crumbling Blocks
    let l7P = blank(), l7F = blank();
    l7P[16] = "S..1...........S"; l7F[16] = "S..2...........S";
    l7P[12] = "S.....CCCC..E..S"; l7F[12] = "S.....cccc..e..S";
    LVL_TEMPLATES.push({ msg: "Brown blocks crumble.", hint: "Move quickly over them.", past: l7P, future: l7F });

    // 8. Combination 1
    let l8P = blank(), l8F = blank();
    l8P[16] = "S..1..C.J.C.E..S"; l8F[16] = "S..2..c.j.c.e..S";
    LVL_TEMPLATES.push({ msg: "", hint: "React quickly.", past: l8P, future: l8F });

    // 9. Phasing Blocks Intro
    let l9P = blank(), l9F = blank();
    l9P[16] = "S..1...........S"; l9F[16] = "S..2...........S";
    l9P[14] = "S.....V........S"; l9F[14] = "S.....v........S";
    l9P[12] = "S.......V......S"; l9F[12] = "S.......v......S";
    l9P[10] = "S.........E....S"; l9F[10] = "S.........e....S";
    LVL_TEMPLATES.push({ msg: "Phasing Blocks blink.", hint: "Time your jumps to the global rhythm.", story: "The fabric of reality began to tear.\\nMatter flickered in and out of existence.", past: l9P, future: l9F });

    // 10. Phasing over pits
    let l10P = blank(), l10F = blank();
    l10P[16] = "S..1.V.V.V..E..S"; l10F[16] = "S..2.v.v.v..e..S";
    LVL_TEMPLATES.push({ msg: "", hint: "Don't stop moving when they are solid.", past: l10P, future: l10F });

    // 11. Conveyors
    let l11P = blank(), l11F = blank();
    l11P[16] = "S..1..++++..E..S"; l11F[16] = "S..2..----..e..S";
    LVL_TEMPLATES.push({ msg: "Conveyor belts push you.", hint: "Fight or ride the belt.", story: "Automated systems continued to run.\\nEndless cycles with no purpose.", past: l11P, future: l11F });

    // 12. Conveyors + Hazards
    let l12P = blank(), l12F = blank();
    l12P[16]= "S..1.++++L..E..S"; l12F[16]= "S..2.----T..e..S";
    LVL_TEMPLATES.push({ msg: "", hint: "Jump before the belt pushes you in.", past: l12P, future: l12F });

    // 13. Advanced Combination
    let l13P = blank(), l13F = blank();
    l13P[16]="S..1.B...>.L.E.S"; l13F[16]="S..2.....<.T.e.S";
    LVL_TEMPLATES.push({ msg: "", hint: "Push the block to hold the door.", past: l13P, future: l13F });

    // 14. Momentum Jump
    let l14P = blank(), l14F = blank();
    l14P[16]="S..1.++++J..E..S"; l14F[16]="S..2.----J..e..S";
    l14P[10]="S...........E..S"; l14F[10]="S...........e..S";
    LVL_TEMPLATES.push({ msg: "Use conveyors for momentum.", hint: "You keep your speed.", past: l14P, future: l14F });

    // 15. The Climb
    let l15P = blank(), l15F = blank();
    l15P[16]="S..1..J........S"; l15F[16]="S..2..j........S";
    l15P[12]="S.......WWW....S"; l15F[12]="S.......www....S";
    l15P[11]="S.......W......S"; l15F[11]="S.......w......S";
    l15P[7] ="S....J..W......S"; l15F[7] ="S....j..w......S";
    l15P[3] ="S..E...........S"; l15F[3] ="S..e...........S";
    LVL_TEMPLATES.push({ msg: "", hint: "Ascend.", story: "Higher into the corrupted spires.", past: l15P, future: l15F });

    // 16. Phasing over Conveyors
    let l16P = blank(), l16F = blank();
    l16P[16]="S..1..V+V+V.E..S"; l16F[16]="S..2..v-v-v.e..S";
    LVL_TEMPLATES.push({ msg: "", hint: "Wait for the phase.", past: l16P, future: l16F });

    // 17. Desync
    let l17P = blank(), l17F = blank();
    l17P[16]="S..1.>.>.>..E..S"; l17F[16]="S..2.<.<.<..e..S";
    LVL_TEMPLATES.push({ msg: "The timelines diverge.", hint: "The future is blocked.", past: l17P, future: l17F });

    // 18. Gauntlet
    let l18P = blank(), l18F = blank();
    l18P[16]="S..1.J.V.V..E..S"; l18F[16]="S..2.j.v.v..e..S";
    LVL_TEMPLATES.push({ msg: "", hint: "Don't fall.", past: l18P, future: l18F });

    // 19. Almost there
    let l19P = blank(), l19F = blank();
    l19P[16]="S..1........E..S"; l19F[16]="S..2........e..S"; 
    l19P[10]="S.V.V.V.E......S"; l19F[10]="S.v.v.v.e......S";
    LVL_TEMPLATES.push({ msg: "", hint: "", story: "You have almost reached the end of time.", past: l19P, future: l19F });

    // 20. The Sync
    let l20P = blank(), l20F = blank();
    l20P[16]="S..1.+++L+++E..S"; l20F[16]="S..2.---T---e..S";
    LVL_TEMPLATES.push({ msg: "The Final Sync.", hint: "", story: "The timelines have fully synchronized.\\nThank you for playing Chrono-Sync.", past: l20P, future: l20F });

}
generateLevels();
"""

html = gen_target.sub(levels_code, html)

# 10. Level Creator palette
palette_target = '<button data-tool="E" style="background:#0fa; color:#000" title="Goal">G</button>'
palette_repl = palette_target + """
                        <button data-tool="+" style="background:#333; color:#0ff" title="Conveyor Right">&gt;&gt;</button>
                        <button data-tool="-" style="background:#333; color:#0ff" title="Conveyor Left">&lt;&lt;</button>
                        <button data-tool="V" style="background:#90f; color:#fff" title="Phasing Block">V</button>"""
html = html.replace(palette_target, palette_repl)

creator_paint_target = "if(char === 'C') char = 'c';"
creator_paint_repl = "if(char === 'C') char = 'c';\n        if(char === 'V') char = 'v';"
html = html.replace(creator_paint_target, creator_paint_repl)

with open('index.html', 'w') as f:
    f.write(html)
