package
{
    import flash.display.MovieClip;

    public dynamic class bairbubbles extends MovieClip
    {

        public var loop:*;

        public function bairbubbles()
        {
            super();
            addFrameScript(0, this.frame1, 33, this.frame34);
        }

        internal function frame1():*
        {
            this.loop = false;
        }

        internal function frame34():*
        {
            stop();
            parent.removeChild(this);
        }


    }
}

