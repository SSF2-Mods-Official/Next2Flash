package
{
    import flash.display.MovieClip;

    public dynamic class uspecSparkle extends MovieClip
    {

        public function uspecSparkle()
        {
            super();
            addFrameScript(4, this.frame5);
        }

        internal function frame5():*
        {
            stop();
            if (parent != null)
            {
                parent.removeChild(this);
            };
        }


    }
}

