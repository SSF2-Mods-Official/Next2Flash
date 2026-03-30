package lucario_fla
{
    import flash.display.MovieClip;

    public dynamic class ItemJab_57 extends MovieClip
    {

        public var aura1:MovieClip;
        public var aura2:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var itemBox:MovieClip;
        public var self:LucarioExt;

        public function ItemJab_57()
        {
            super();
            addFrameScript(0, this.frame1, 3, this.frame4, 4, this.frame5, 8, this.frame9, 9, this.frame10, 10, this.frame11, 12, this.frame13);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as LucarioExt);
            if (SSF2API.isReady() && this.self)
            {
                this.self.updateAuraPaws();
            };
        }

        internal function frame4():*
        {
            this.self.getItem().activateItem();
            this.self.playAttackSound(1);
            this.self.updateAuraPaws();
            this.self.attachEffect("global_dust_light", {"x":this.self.flipX(-10)});
        }

        internal function frame5():*
        {
            this.self.getItem().deactivateItem();
        }

        internal function frame9():*
        {
            this.self.updateAuraPaws();
        }

        internal function frame10():*
        {
            this.self.updateAuraPaws();
        }

        internal function frame11():*
        {
            this.self.updateAuraPaws();
        }

        internal function frame13():*
        {
            this.self.endAttack();
        }


    }
}

