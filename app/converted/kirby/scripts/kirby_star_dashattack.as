package
{
    import flash.display.MovieClip;

    public dynamic class kirby_star_dashattack extends MovieClip
    {

        public function kirby_star_dashattack()
        {
            super();
            addFrameScript(14, this.frame15);
        }

        internal function frame15():*
        {
            if (parent != null)
            {
                parent.removeChild(this);
            };
        }


    }
}

