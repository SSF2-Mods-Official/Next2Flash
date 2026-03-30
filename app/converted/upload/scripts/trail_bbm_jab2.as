package
{
    import flash.display.MovieClip;

    public dynamic class trail_bbm_jab2 extends MovieClip
    {

        public function trail_bbm_jab2()
        {
            super();
            addFrameScript(4, this.frame5);
        }

        internal function frame5():*
        {
            stop();
            if (parent)
            {
                parent.removeChild(this);
            };
        }


    }
}

