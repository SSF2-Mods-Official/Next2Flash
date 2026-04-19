package blackmage_fla {
    import flash.display.DisplayObject;
    import flash.display.MovieClip;
    import flash.events.Event;
    public dynamic class Lose_13 extends MovieClip {
        public function Lose_13() {
            super();
            addFrameScript(49, frame_50);
        }
        internal function frame_50():* {
            gotoAndPlay("redo");
        }
    }
}
