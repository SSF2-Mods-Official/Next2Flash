package
{
    import flash.display.MovieClip;

    public dynamic class bmanFSBomb extends MovieClip
    {

        public var stance:MovieClip;

        public function bmanFSBomb()
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

