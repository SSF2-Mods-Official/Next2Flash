package blackmage_fla {
    import flash.display.DisplayObject;
    import flash.display.MovieClip;
    import flash.events.Event;
    import flash.geom.Point;
    public dynamic class FinalSmash_131 extends MovieClip {
        public var itemBox:MovieClip;
        public var self:BlackMageExt;
        public var warriorProj:*;
        public var thiefProj:*;
        public var wmageProj:*;
        public var fsTargets:Array;
        public var holy:Point;
        public function FinalSmash_131() {
            super();
            addFrameScript(0, frame_1);
            addFrameScript(11, frame_12);
            addFrameScript(14, frame_15);
            addFrameScript(24, frame_25);
            addFrameScript(25, frame_26);
            addFrameScript(55, frame_56);
            addFrameScript(84, frame_85);
            addFrameScript(85, frame_86);
            addFrameScript(115, frame_116);
            addFrameScript(116, frame_117);
        }
        internal function frame_1():* {
            var itemBox:MovieClip;
            var self:BlackMageExt;
            var warriorProj:*;
            var thiefProj:*;
            var wmageProj:*;
            var fsTargets:Array;
            var holy:Point;
            if (SSF2API.isReady())
                        {
                            this.self = (SSF2API.getCharacter(this) as BlackMageExt);
                        };
                        this.warriorProj = null;
                        this.thiefProj = null;
                        this.wmageProj = null;
                        this.fsTargets = new Array();
                        if (parent && SSF2API.isReady())
                        {
                            this.self.setGlobalVariable("fsTargets", this.fsTargets);
                            this.self.unnattachFromGround();
                        };
        }
        internal function frame_12():* {
            SSF2API.getCamera().shake(10);
                        this.self.playSound("bm_Warp_part2");
                        this.warriorProj = this.self.fireProjectile("bm_fs_warrior");
                        this.warriorProj.addToCamera();
                        this.self.attachEffect("bm_fs_warp", {"x":this.self.flipX(-50)});
        }
        internal function frame_15():* {
            SSF2API.getCamera().shake(10);
                        this.self.playSound("bm_Warp_part2");
                        this.thiefProj = this.self.fireProjectile("bm_fs_thief");
                        this.thiefProj.addToCamera();
                        this.self.attachEffect("bm_fs_warp", {"x":this.self.flipX(50)});
                        this.self.createTimer(1, 0, this.checkFSTargets);
        }
        internal function frame_25():* {
            this.self.stancePlayFrame("waitloop");
        }
        internal function frame_26():* {
            SSF2API.getCamera().shake(10);
                        this.self.playSound("bm_Warp_part2");
                        this.wmageProj = this.self.fireProjectile("bm_fs_wmage");
                        this.wmageProj.addToCamera();
                        this.self.attachEffect("bm_fs_warp", {"x":this.self.flipX(80)});
        }
        internal function frame_56():* {
            if (this.self.getCurrentProjectile() != null)
                        {
                            this.holy = new Point(this.self.getCurrentProjectile().getX(), this.self.getCurrentProjectile().getY());
                            this.self.fireProjectile("bm_fs_flare", this.holy.x, (this.holy.y - 125), true);
                        };
        }
        internal function frame_85():* {
            this.self.forceOnGround(5);
                        if (!this.self.isOnGround())
                        {
                            this.self.resetMovement();
                            this.self.updateAttackStats({"allowControl":true});
                            this.self.resetJumps();
                            this.self.toJump();
                        };
        }
        internal function frame_86():* {
            this.fsTargets = null;
                        this.self.endAttack();
        }
        internal function frame_116():* {
            this.self.forceOnGround(5);
                        if (!this.self.isOnGround())
                        {
                            this.self.updateAttackStats({"allowControl":true});
                            this.self.resetJumps();
                            this.self.toJump();
                        };
        }
        internal function frame_117():* {
            this.fsTargets = null;
                        this.self.endAttack();
        }
    }
}
