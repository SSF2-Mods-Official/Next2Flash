package blackmage_fla {
    import flash.display.DisplayObject;
    import flash.display.MovieClip;
    import flash.events.Event;
    public dynamic class DodgeRoll_109 extends MovieClip {
        public var hitBox:MovieClip;
        public var itemBox:MovieClip;
        public var self:BlackMageExt;
        public var effect:*;
        public function DodgeRoll_109() {
            super();
            addFrameScript(0, frame_1);
            addFrameScript(1, frame_2);
            addFrameScript(2, frame_3);
            addFrameScript(8, frame_9);
            addFrameScript(15, frame_16);
        }
        internal function frame_1():* {
            var hitBox:MovieClip;
            var itemBox:MovieClip;
            var self:BlackMageExt;
            var effect:*;
            if (SSF2API.isReady())
                        {
                            this.self = (SSF2API.getCharacter(this) as BlackMageExt);
                        };
        }
        internal function frame_2():* {
            this.effect = this.self.attachEffect("global_dust_heavy", {
                            "scaleX":0.8,
                            "scaleY":0.8
                        });
                        this.effect.scaleX = -(this.effect.scaleX);
        }
        internal function frame_3():* {
            this.self.setIntangibility(true);
        }
        internal function frame_9():* {
            this.self.setIntangibility(false);
        }
        internal function frame_16():* {
            this.self.endAttack();
        }
    }
}
