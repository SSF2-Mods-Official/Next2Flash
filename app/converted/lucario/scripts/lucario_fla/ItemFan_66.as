package lucario_fla
{
    import flash.display.MovieClip;

    public dynamic class ItemFan_66 extends MovieClip
    {

        public var aura1:MovieClip;
        public var aura2:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var itemBox:MovieClip;
        public var self:LucarioExt;

        public function ItemFan_66()
        {
            super();
            addFrameScript(0, this.frame1, 2, this.frame3, 3, this.frame4, 4, this.frame5, 5, this.frame6);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as LucarioExt);
            if (SSF2API.isReady() && this.self)
            {
                this.self.updateAuraPaws();
            };
        }

        internal function frame3():*
        {
            this.self.getItem().activateItem();
            this.self.playAttackSound(1);
            this.self.updateAuraPaws();
            this.self.attachEffect("global_dust_light", {"x":this.self.flipX(-10)});
        }

        internal function frame4():*
        {
            this.self.getItem().deactivateItem();
        }

        internal function frame5():*
        {
            this.self.updateAuraPaws();
        }

        internal function frame6():*
        {
            this.self.endAttack();
        }


    }
}

