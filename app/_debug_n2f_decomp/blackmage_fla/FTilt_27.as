package blackmage_fla {
    import flash.display.DisplayObject;
    import flash.display.MovieClip;
    import flash.events.Event;
    public dynamic class FTilt_27 extends MovieClip {
        public var attackBox:MovieClip;
        public var attackBox2:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var itemBox:MovieClip;
        public var self:BlackMageExt;
        public function FTilt_27() {
            super();
            addFrameScript(0, frame_1);
            addFrameScript(2, frame_3);
            addFrameScript(3, frame_4);
            addFrameScript(14, frame_15);
        }
        internal function frame_1():* {
            var attackBox:MovieClip;
            var attackBox2:MovieClip;
            var hitBox:MovieClip;
            var hitBox2:MovieClip;
            var itemBox:MovieClip;
            var self:BlackMageExt;
            if (SSF2API.isReady())
                        {
                            this.self = (SSF2API.getCharacter(this) as BlackMageExt);
                        };
        }
        internal function frame_3():* {
            this.self.addEffectToList(this.self.attachEffect("trail_bmage_ftilt", {
                            "scaleX":1.4,
                            "scaleY":1.4,
                            "parentLock":true,
                            "syncHitStun":true
                        }));
                        this.self.clearEffectsOnStateChange();
        }
        internal function frame_4():* {
            this.self.playAttackSound(1);
                        this.self.attachEffect("global_dust_light");
        }
        internal function frame_15():* {
            this.self.endAttack();
        }
    }
}
