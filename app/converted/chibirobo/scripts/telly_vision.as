package
{
    import flash.display.MovieClip;

    public dynamic class telly_vision extends MovieClip
    {

        public var stance:MovieClip;

        public function telly_vision()
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
            stop();
        }


    }
}

