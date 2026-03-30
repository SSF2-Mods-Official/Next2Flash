package
{
    import flash.display.MovieClip;

    public dynamic class ddd_bigMissile extends MovieClip
    {

        public var stance:MovieClip;

        public function ddd_bigMissile()
        {
            super();
            addFrameScript(0, this.frame1);
        }

        internal function frame1():*
        {
            stop();
        }


    }
}

