package
{
    import flash.display.MovieClip;

    public dynamic class lucario_fsbeam extends MovieClip
    {

        public var stance:MovieClip;

        public function lucario_fsbeam()
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

