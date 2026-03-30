package
{
    import flash.display.MovieClip;

    public dynamic class dairSparkle extends MovieClip
    {

        public function dairSparkle()
        {
            super();
            addFrameScript(10, this.frame11);
        }

        internal function frame11():*
        {
            stop();
            if (parent != null)
            {
                parent.removeChild(this);
            };
        }


    }
}

