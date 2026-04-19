package blackmage_fla {
    import flash.display.DisplayObject;
    import flash.display.MovieClip;
    import flash.events.Event;
    public dynamic class AirDodge_110 extends MovieClip {
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:BlackMageExt;
        public function AirDodge_110() {
            super();
            addFrameScript(0, frame_1);
            addFrameScript(2, frame_3);
            addFrameScript(14, frame_15);
            addFrameScript(23, frame_24);
        }
        internal function frame_1():* {
            var hitBox:MovieClip;
            var hitBox2:MovieClip;
            var hitBox3:MovieClip;
            var itemBox:MovieClip;
            var self:BlackMageExt;
            this.self = (SSF2API.getCharacter(this) as BlackMageExt);
        }
        internal function frame_3():* {
            this.self.setIntangibility(true);
                        this.self.addEventListener(SSF2Event.GROUND_TOUCH, this.dodgeLand);
        }
        internal function frame_15():* {
            this.self.setIntangibility(false);
        }
        internal function frame_24():* {
            this.self.endAttack();
        }
    }
}
