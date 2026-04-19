package blackmage_fla {
    import flash.display.DisplayObject;
    import flash.display.MovieClip;
    import flash.events.Event;
    public dynamic class Crouch_104 extends MovieClip {
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var itemBox:MovieClip;
        public var self:BlackMageExt;
        public function Crouch_104() {
            super();
            addFrameScript(0, frame_1);
            addFrameScript(3, frame_4);
            addFrameScript(8, frame_9);
        }
        internal function frame_1():* {
            var hitBox:MovieClip;
            var hitBox2:MovieClip;
            var itemBox:MovieClip;
            var self:BlackMageExt;
            if (SSF2API.isReady())
                        {
                            this.self = (SSF2API.getCharacter(this) as BlackMageExt);
                        };
        }
        internal function frame_4():* {
            this.self.setGlobalVariable("crouchdown", true);
        }
        internal function frame_9():* {
            this.self.stancePlayFrame("loop");
        }
    }
}
