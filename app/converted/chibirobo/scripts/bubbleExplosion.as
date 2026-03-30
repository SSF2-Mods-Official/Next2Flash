package
{
    import flash.display.MovieClip;

    public dynamic class bubbleExplosion extends MovieClip
    {

        public var loop:*;

        public function bubbleExplosion()
        {
            super();
            addFrameScript(0, this.frame1, 25, this.frame26);
        }

        internal function frame1():*
        {
            this.loop = false;
        }

        internal function frame26():*
        {
            stop();
            parent.removeChild(this);
        }


    }
}

