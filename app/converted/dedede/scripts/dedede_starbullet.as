package
{
    import flash.display.MovieClip;

    public dynamic class dedede_starbullet extends MovieClip
    {

        public var stance:MovieClip;

        public function dedede_starbullet()
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

