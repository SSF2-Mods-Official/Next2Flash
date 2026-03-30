package lucario_fla
{
    import flash.display.MovieClip;

    public dynamic class ItemThrows_Air__76 extends MovieClip
    {

        public var aura1:MovieClip;
        public var aura2:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var itemBox:MovieClip;
        public var self:LucarioExt;

        public function ItemThrows_Air__76()
        {
            super();
            addFrameScript(0, this.frame1, 1, this.frame2, 3, this.frame4, 10, this.frame11, 11, this.frame12, 12, this.frame13, 14, this.frame15, 15, this.frame16, 17, this.frame18, 20, this.frame21, 22, this.frame23, 23, this.frame24, 24, this.frame25, 26, this.frame27, 29, this.frame30, 34, this.frame35, 35, this.frame36, 36, this.frame37, 38, this.frame39, 39, this.frame40, 46, this.frame47);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as LucarioExt);
            if (SSF2API.isReady() && this.self)
            {
                this.self.updateAuraPaws();
            };
        }

        internal function frame2():*
        {
            this.self.attachEffect("global_dust_swirl");
        }

        internal function frame4():*
        {
            this.self.tossItem(158);
        }

        internal function frame11():*
        {
            this.self.endAttack();
        }

        internal function frame12():*
        {
            this.self.updateAuraPaws();
        }

        internal function frame13():*
        {
            this.self.attachEffect("global_dust_swirl");
        }

        internal function frame15():*
        {
            this.self.updateAuraPaws();
            this.self.tossItem(270);
        }

        internal function frame16():*
        {
            this.self.updateAuraPaws();
        }

        internal function frame18():*
        {
            this.self.updateAuraPaws();
        }

        internal function frame21():*
        {
            this.self.updateAuraPaws();
        }

        internal function frame23():*
        {
            this.self.endAttack();
        }

        internal function frame24():*
        {
            this.self.updateAuraPaws();
        }

        internal function frame25():*
        {
            this.self.updateAuraPaws();
            this.self.attachEffect("global_dust_swirl");
        }

        internal function frame27():*
        {
            this.self.updateAuraPaws();
            this.self.tossItem(90);
        }

        internal function frame30():*
        {
            this.self.updateAuraPaws();
        }

        internal function frame35():*
        {
            this.self.endAttack();
        }

        internal function frame36():*
        {
            this.self.updateAuraPaws();
        }

        internal function frame37():*
        {
            this.self.updateAuraPaws();
            this.self.attachEffect("global_dust_swirl");
        }

        internal function frame39():*
        {
            this.self.updateAuraPaws();
            this.self.tossItem(12);
        }

        internal function frame40():*
        {
            this.self.updateAuraPaws();
        }

        internal function frame47():*
        {
            this.self.endAttack();
        }


    }
}

