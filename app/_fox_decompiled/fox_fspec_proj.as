package
{
    import flash.display.MovieClip;

    public dynamic class fox_fspec_proj extends MovieClip
    {

        public var stance:MovieClip;

        public function fox_fspec_proj()
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

