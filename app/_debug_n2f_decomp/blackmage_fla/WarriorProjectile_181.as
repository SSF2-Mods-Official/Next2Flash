package blackmage_fla {
    import flash.display.DisplayObject;
    import flash.display.MovieClip;
    import flash.events.Event;
    public dynamic class WarriorProjectile_181 extends MovieClip {
        public var attackBox:MovieClip;
        public var self:*;
        public var jumpedToSwing:Boolean;
        public var oldX:Number;
        public var stuckCount:Number;
        public var character:*;
        public var temp:*;
        public function WarriorProjectile_181() {
            super();
            addFrameScript(0, frame_1);
            addFrameScript(9, frame_10);
            addFrameScript(10, frame_11);
            addFrameScript(11, frame_12);
            addFrameScript(12, frame_13);
            addFrameScript(13, frame_14);
            addFrameScript(20, frame_21);
            addFrameScript(21, frame_22);
            addFrameScript(23, frame_24);
            addFrameScript(26, frame_27);
            addFrameScript(38, frame_39);
            addFrameScript(42, frame_43);
            addFrameScript(43, frame_44);
            addFrameScript(52, frame_53);
        }
        internal function frame_1():* {
            var attackBox:MovieClip;
            var self:*;
            var jumpedToSwing:Boolean;
            var oldX:Number;
            var stuckCount:Number;
            var character:*;
            var temp:*;
            this.self = SSF2API.getProjectile(this);
                        this.jumpedToSwing = false;
                        this.oldX = 0;
                        this.stuckCount = 0;
                        if (SSF2API.isReady() && this.self)
                        {
                            this.character = this.self.getOwner();
                            this.self.updateAttackStats({"air_ease":0});
                            this.self.addEventListener(SSF2Event.ATTACK_HIT, this.onHit);
                            this.self.createTimer(1, 0, this.checkActivation);
                        };
        }
        internal function frame_10():* {
            this.self.setXSpeed(4, false);
                        this.self.createTimer(1, 0, this.checkStuck);
        }
        internal function frame_11():* {
            this.self.setXSpeed(8, false);
        }
        internal function frame_12():* {
            this.self.setXSpeed(13, false);
        }
        internal function frame_13():* {
            this.self.setXSpeed(18, false);
                        this.self.attachEffect("global_dust_heavy");
        }
        internal function frame_14():* {
            this.self.setXSpeed(28, false);
        }
        internal function frame_21():* {
            this.self.stancePlayFrame("loop");
        }
        internal function frame_22():* {
            this.self.setXSpeed(18, false);
        }
        internal function frame_24():* {
            this.self.setXSpeed(5, false);
        }
        internal function frame_27():* {
            this.self.setXSpeed(0);
        }
        internal function frame_39():* {
            this.self.setXSpeed(-5, false);
                        this.self.setYSpeed(-10);
                        this.self.updateProjectileStats({
                            "gravity":1.5,
                            "maxgravity":12
                        });
                        this.self.updateAttackStats({"air_ease":-1});
                        this.self.addEventListener(SSF2Event.GROUND_TOUCH, this.land);
        }
        internal function frame_43():* {
            this.self.stancePlayFrame("landwait");
        }
        internal function frame_44():* {
            this.self.attachEffect("bm_fs_warp");
                        this.self.playSound("bm_Warp_part2");
        }
        internal function frame_53():* {
            this.self.destroy();
        }
    }
}
