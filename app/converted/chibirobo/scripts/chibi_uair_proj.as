package
{
    import flash.display.MovieClip;

    public dynamic class chibi_uair_proj extends MovieClip
    {

        public var stance:MovieClip;

        public function chibi_uair_proj()
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

