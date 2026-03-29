package gameandwatch_fla
{
    import flash.display.MovieClip;

    public dynamic class ItemDashAttack_66 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var hitBox5:MovieClip;
        public var itemBox:MovieClip;
        public var self:gameandwatchExt;

        public function ItemDashAttack_66()
        {
            super();
            addFrameScript(0, this.frame1, 1, this.frame2, 5, this.frame6, 6, this.frame7, 7, this.frame8, 14, this.frame15, 15, this.frame16, 23, this.frame24);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as gameandwatchExt);
            if (parent && SSF2API.isReady() && this.self)
            {
                this.self.setXSpeed(25, false);
            };
        }

        internal function frame2():*
        {
            this.self.setXSpeed(0, false);
        }

        internal function frame6():*
        {
            this.self.getItem().activateItem();
            this.self.playSound("gw_dtilt");
            this.self.setXSpeed(30, false);
            this.self.attachEffect("global_dust_heavy");
        }

        internal function frame7():*
        {
            this.self.setXSpeed(0, false);
        }

        internal function frame8():*
        {
            this.self.getItem().deactivateItem();
        }

        internal function frame15():*
        {
            this.self.setXSpeed(35, false);
        }

        internal function frame16():*
        {
            this.self.setXSpeed(0, false);
        }

        internal function frame24():*
        {
            this.self.endAttack();
        }


    }
}

