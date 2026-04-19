package
{
    import flash.display.MovieClip;

    public dynamic class bm_fthrow_proj extends MovieClip
    {

        public var stance:MovieClip;

        public function bm_fthrow_proj()
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

