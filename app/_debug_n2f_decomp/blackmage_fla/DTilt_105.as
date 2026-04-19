package blackmage_fla {
    import flash.display.DisplayObject;
    import flash.display.MovieClip;
    import flash.events.Event;
    public dynamic class DTilt_105 extends MovieClip {
        public var attackBox:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var itemBox:MovieClip;
        public var self:BlackMageExt;
        public function DTilt_105() {
            super();
            addFrameScript(0, frame_1);
            addFrameScript(2, frame_3);
            addFrameScript(3, frame_4);
            addFrameScript(5, frame_6);
            addFrameScript(13, frame_14);
        }
        internal function frame_1():* {
            var attackBox:MovieClip;
            var hitBox:MovieClip;
            var hitBox2:MovieClip;
            var itemBox:MovieClip;
            var self:BlackMageExt;
            this.self = (SSF2API.getCharacter(this) as BlackMageExt);
                        if (SSF2API.isReady() && this.self)
                        {
                            this.self.attachEffect("global_spark");
                        };
        }
        internal function frame_3():* {
            this.self.attachEffect("global_dust_light");
                        this.self.setXSpeed(3, false);
                        this.self.playSound("bm_knife");
        }
        internal function frame_4():* {
            this.self.addEffectToList(this.self.attachEffect("trail_bmage_dtilt", {
                            "scaleX":1.4,
                            "scaleY":1.4,
                            "parentLock":true,
                            "syncHitStun":true
                        }));
                        this.self.clearEffectsOnStateChange();
        }
        internal function frame_6():* {
            this.self.attachEffect("global_dust_blast", {
                            "x":this.self.flipX(30),
                            "y":-2,
                            "parentLock":true
                        });
        }
        internal function frame_14():* {
            this.self.endAttack();
        }
    }
}
