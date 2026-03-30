package bomberman_fla
{
    import flash.display.MovieClip;

    public dynamic class bomberman_techground_105 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:BombermanExt;

        public function bomberman_techground_105()
        {
            super();
            addFrameScript(0, this.frame1, 10, this.frame11, 13, this.frame14);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as BombermanExt);
            if (parent && SSF2API.isReady() && this.self)
            {
                this.self.setIntangibility(true);
            };
        }

        internal function frame11():*
        {
            this.self.setIntangibility(false);
        }

        internal function frame14():*
        {
            this.self.endAttack();
        }


    }
}

