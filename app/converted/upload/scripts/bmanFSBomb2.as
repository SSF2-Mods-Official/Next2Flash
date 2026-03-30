package
{
    import flash.display.MovieClip;

    public dynamic class bmanFSBomb2 extends MovieClip
    {

        public var stance:MovieClip;

        public function bmanFSBomb2()
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

