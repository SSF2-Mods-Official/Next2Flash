package bomberman_fla
{
    import flash.display.MovieClip;

    public dynamic class bomberman_rollground_86 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:BombermanExt;

        public function bomberman_rollground_86()
        {
            super();
            addFrameScript(0, this.frame1, 10, this.frame11, 17, this.frame18);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as BombermanExt);
            if (parent && SSF2API.isReady())
            {
                this.self.setIntangibility(true);
            };
        }

        internal function frame11():*
        {
            this.self.setIntangibility(false);
        }

        internal function frame18():*
        {
            this.self.endAttack();
        }


    }
}

