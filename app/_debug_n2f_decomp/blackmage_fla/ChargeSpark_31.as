package blackmage_fla {
    import flash.display.DisplayObject;
    import flash.display.MovieClip;
    import flash.events.Event;
    public dynamic class ChargeSpark_31 extends MovieClip {
        public function ChargeSpark_31() {
            super();
            addFrameScript(4, frame_5);
        }
        internal function frame_5():* {
            stop();
                        parent.removeChild(this);
        }
    }
}
