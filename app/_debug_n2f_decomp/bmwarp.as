package {
    import flash.display.DisplayObject;
    import flash.display.MovieClip;
    import flash.events.Event;
    public dynamic class bmwarp extends MovieClip {
        public var stance:MovieClip;
        public function bmwarp() {
            super();
            addFrameScript(0, frame_1);
        }
        internal function frame_1():* {
            var stance:MovieClip;
            stop();
        }
    }
}
