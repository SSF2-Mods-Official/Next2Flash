package
{
    import flash.display.MovieClip;

    public dynamic class chibi_nair_proj extends MovieClip
    {

        public var stance:MovieClip;

        public function chibi_nair_proj()
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

