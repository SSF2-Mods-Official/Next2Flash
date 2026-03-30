package
{
    import flash.display.MovieClip;

    public dynamic class simon_coffin_proj extends MovieClip
    {

        public var stance:MovieClip;

        public function simon_coffin_proj()
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

