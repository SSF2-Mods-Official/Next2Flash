package {
    import flash.display.DisplayObject;
    import flash.display.MovieClip;
    import flash.events.Event;
    public dynamic class blackmage_dash_attack extends MovieClip {
        public function blackmage_dash_attack() {
            super();
            addFrameScript(18, frame_19);
        }
        internal function frame_19():* {
            stop();
                        if (parent)
                        {
                            parent.removeChild(this);
                        };
        }
    }
}
