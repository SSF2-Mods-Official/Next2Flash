package
{
    import flash.display.MovieClip;

    public dynamic class trail_lucario_jab3 extends MovieClip
    {

        public function trail_lucario_jab3()
        {
            super();
            addFrameScript(5, this.frame6);
        }

        internal function frame6():*
        {
            if (parent)
            {
                parent.removeChild(this);
            };
        }


    }
}

