package blackmage_fla {
    import flash.display.DisplayObject;
    import flash.display.MovieClip;
    import flash.events.Event;
    public dynamic class Win_12 extends MovieClip {
        public var self:BlackMageExt;
        public function Win_12() {
            super();
            addFrameScript(0, frame_1);
            addFrameScript(125, frame_126);
        }
        internal function frame_1():* {
            var self:BlackMageExt;
            this.self = (SSF2API.getCharacter(this) as BlackMageExt);
        }
        internal function frame_126():* {
            gotoAndPlay("loop");
        }
    }
}
