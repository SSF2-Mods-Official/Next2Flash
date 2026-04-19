package
{
    import flash.display.MovieClip;

    public dynamic class bm_waterSpout_strong extends MovieClip
    {

        public var stance:MovieClip;

        public function bm_waterSpout_strong()
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

