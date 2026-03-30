package
{
    import flash.display.MovieClip;

    public dynamic class bomber_globalSpark extends MovieClip
    {

        public function bomber_globalSpark()
        {
            super();
            addFrameScript(4, this.frame5, 5, this.frame6);
        }

        internal function frame5():*
        {
            stop();
            parent.removeChild(this);
        }

        internal function frame6():*
        {
            gotoAndPlay("end");
        }


    }
}

