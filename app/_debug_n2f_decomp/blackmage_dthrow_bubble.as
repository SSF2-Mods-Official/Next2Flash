package {
    import flash.display.DisplayObject;
    import flash.display.MovieClip;
    import flash.events.Event;
    public dynamic class blackmage_dthrow_bubble extends MovieClip {
        public function blackmage_dthrow_bubble() {
            super();
            addFrameScript(12, frame_13);
        }
        internal function frame_13():* {
            stop();
                        if (parent)
                        {
                            parent.removeChild(this);
                        };
        }
    }
}
