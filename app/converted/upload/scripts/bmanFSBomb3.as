package
{
    import flash.display.MovieClip;

    public dynamic class bmanFSBomb3 extends MovieClip
    {

        public var stance:MovieClip;

        public function bmanFSBomb3()
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

