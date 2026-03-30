package lucario_fla
{
    import flash.display.MovieClip;

    public dynamic class ItemHome_Run_62 extends MovieClip
    {

        public var aura1:MovieClip;
        public var aura2:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var itemBox:MovieClip;
        public var self:LucarioExt;

        public function ItemHome_Run_62()
        {
            super();
            addFrameScript(0, this.frame1, 4, this.frame5, 10, this.frame11, 16, this.frame17, 22, this.frame23, 28, this.frame29, 30, this.frame31, 32, this.frame33, 39, this.frame40, 41, this.frame42, 43, this.frame44, 45, this.frame46);
        }

        public function effects():void
        {
            this.self.attachEffect("global_dust_heavy", {
                "x":this.self.flipX(5),
                "y":3,
                "scaleX":-0.5,
                "scaleY":-0.5
            });
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as LucarioExt);
            if (this.self && SSF2API.isReady())
            {
                this.self.createTimer(4, -1, this.effects);
                this.self.updateAuraPaws();
            };
        }

        internal function frame5():*
        {
            this.self.updateAuraPaws();
        }

        internal function frame11():*
        {
            this.self.updateAuraPaws();
        }

        internal function frame17():*
        {
            this.self.updateAuraPaws();
        }

        internal function frame23():*
        {
            this.self.updateAuraPaws();
        }

        internal function frame29():*
        {
            this.self.destroyTimer(this.effects);
            this.self.updateAttackStats({"superArmor":true});
            this.self.updateAuraPaws();
        }

        internal function frame31():*
        {
            this.self.getItem().activateItem();
            this.self.playAttackSound(1);
            this.self.playVoiceSound(1);
            SSF2API.getCamera().shake(6);
            this.self.attachEffect("global_dust_heavy", {
                "x":this.self.flipX(5),
                "y":3,
                "scaleX":-0.75,
                "scaleY":-0.75
            });
            this.self.updateAuraPaws();
        }

        internal function frame33():*
        {
            this.self.getItem().deactivateItem();
            this.self.updateAttackStats({"superArmor":false});
        }

        internal function frame40():*
        {
            this.self.updateAuraPaws();
        }

        internal function frame42():*
        {
            this.self.updateAuraPaws();
        }

        internal function frame44():*
        {
            this.self.updateAuraPaws();
        }

        internal function frame46():*
        {
            this.self.endAttack();
        }


    }
}

