package
{
    import flash.display.MovieClip;

    public dynamic class floorTwinkle extends MovieClip
    {

        public var loop:*;

        public function floorTwinkle()
        {
            super();
            addFrameScript(0, this.frame1, 75, this.frame76);
        }

        internal function frame1():*
        {
            this.loop = false;
        }

        internal function frame76():*
        {
            stop();
            parent.removeChild(this);
        }


    }
}

