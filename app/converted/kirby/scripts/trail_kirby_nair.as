package
{
    import flash.display.MovieClip;

    public dynamic class trail_kirby_nair extends MovieClip
    {

        public function trail_kirby_nair()
        {
            super();
            addFrameScript(17, this.frame18);
        }

        internal function frame18():*
        {
            if (parent)
            {
                parent.removeChild(this);
            };
        }


    }
}

