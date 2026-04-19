package
{
    import flash.display.MovieClip;

    public dynamic class blackmage_demieffect extends MovieClip
    {

        public function blackmage_demieffect()
        {
            super();
            addFrameScript(17, this.frame18);
        }

        internal function frame18():*
        {
            stop();
            if (parent != null)
            {
                parent.removeChild(this);
            };
        }


    }
}

