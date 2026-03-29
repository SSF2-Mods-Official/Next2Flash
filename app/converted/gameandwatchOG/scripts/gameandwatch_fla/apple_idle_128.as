package gameandwatch_fla
{
    import flash.display.MovieClip;

    public dynamic class apple_idle_128 extends MovieClip
    {

        public var catchBox:MovieClip;

        public function apple_idle_128()
        {
            super();
            addFrameScript(0, this.frame1, 1, this.frame2);
        }

        internal function frame1():*
        {
            stop();
        }

        internal function frame2():*
        {
            gotoAndStop((this.currentFrame - 1));
        }


    }
}

