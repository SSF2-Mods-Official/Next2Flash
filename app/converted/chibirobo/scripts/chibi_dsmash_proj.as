package
{
    import flash.display.MovieClip;

    public dynamic class chibi_dsmash_proj extends MovieClip
    {

        public var stance:MovieClip;

        public function chibi_dsmash_proj()
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

