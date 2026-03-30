package
{
    import flash.display.MovieClip;

    public dynamic class dedede_gordo extends MovieClip
    {

        public var stance:MovieClip;

        public function dedede_gordo()
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

