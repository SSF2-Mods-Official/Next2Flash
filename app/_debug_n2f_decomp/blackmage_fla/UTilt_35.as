package blackmage_fla {
    import flash.display.DisplayObject;
    import flash.display.MovieClip;
    import flash.events.Event;
    public dynamic class UTilt_35 extends MovieClip {
        public var attackBox:MovieClip;
        public var attackBox2:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:BlackMageExt;
        public function UTilt_35() {
            super();
            addFrameScript(0, frame_1);
            addFrameScript(1, frame_2);
            addFrameScript(13, frame_14);
            addFrameScript(14, frame_15);
        }
        internal function frame_1():* {
            var attackBox:MovieClip;
            var attackBox2:MovieClip;
            var hitBox:MovieClip;
            var hitBox2:MovieClip;
            var hitBox3:MovieClip;
            var itemBox:MovieClip;
            var self:BlackMageExt;
            if (SSF2API.isReady())
                        {
                            this.self = (SSF2API.getCharacter(this) as BlackMageExt);
                        };
                        if (parent && SSF2API.isReady())
                        {
                            this.self.attachEffect("global_spark", {
                                "x":this.self.flipX(-7),
                                "y":-13
                            });
                        };
        }
        internal function frame_2():* {
            this.self.attachEffect("global_dust_light");
                        this.self.playAttackSound(1);
                        this.self.addEffectToList(this.self.attachEffect("trail_bmage_utilt", {
                            "scaleX":1.4,
                            "scaleY":1.4,
                            "parentLock":true,
                            "syncHitStun":true
                        }));
                        this.self.clearEffectsOnStateChange();
                        this.self.setXSpeed((this.self.getXSpeed() * 0.75));
        }
        internal function frame_14():* {
            if (this.self.getMetalStatus())
                        {
                            this.self.playSound("metal_step_s1");
                        };
        }
        internal function frame_15():* {
            this.self.endAttack();
        }
    }
}
