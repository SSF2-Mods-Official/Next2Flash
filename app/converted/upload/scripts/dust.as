package
{
    import flash.display.MovieClip;

    public dynamic class dust extends MovieClip
    {

        public function dust()
        {
            super();
            addFrameScript(10, this.frame11);
        }

        internal function frame11():*
        {
            if ((root != null) && (parent != null))
            {
                parent.removeChild(this);
            };
        }


    }
}

