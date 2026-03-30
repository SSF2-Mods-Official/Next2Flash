package
{
    import flash.display.MovieClip;

    public dynamic class chibi_lazor extends MovieClip
    {

        public var stance:MovieClip;

        public function chibi_lazor()
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

