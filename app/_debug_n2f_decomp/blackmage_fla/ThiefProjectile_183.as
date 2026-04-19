package blackmage_fla {
    import flash.display.DisplayObject;
    import flash.display.MovieClip;
    import flash.events.Event;
    public dynamic class ThiefProjectile_183 extends MovieClip {
        public var attackBox:MovieClip;
        public var self:*;
        public var jumpedToSwing:Boolean;
        public var oldX:Number;
        public var stuckCount:Number;
        public var character:*;
        public var temp:*;
        public function ThiefProjectile_183() {
            super();
            addFrameScript(0, frame_1);
            addFrameScript(10, frame_11);
            addFrameScript(11, frame_12);
            addFrameScript(28, frame_29);
            addFrameScript(38, frame_39);
            addFrameScript(45, frame_46);
            addFrameScript(50, frame_51);
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
                            this.self.addEventListener(SSF2Event.ATTACK_HIT, this.onHit);
                            this.self.createTimer(1, 0, this.checkActivation);
                        };
        }
        internal function frame_11():* {
            this.self.attachEffect("global_dust_cloud");
        }
        internal function frame_12():* {
            this.self.setXSpeed(28, false);
                        this.self.setYSpeed(-20);
                        this.self.updateProjectileStats({
                            "gravity":1.5,
                            "maxgravity":12
                        });
                        this.self.addEventListener(SSF2Event.GROUND_TOUCH, this.land);
                        this.self.createTimer(1, 0, this.checkStuck);
        }
        internal function frame_29():* {
            this.self.stancePlayFrame("loop");
        }
        internal function frame_39():* {
            this.self.stancePlayFrame("endLoop");
        }
        internal function frame_46():* {
            this.self.attachEffect("bm_fs_warp");
                        this.self.playSound("bm_Warp_part2");
        }
        internal function frame_51():* {
            this.self.destroy();
        }
    }
}
