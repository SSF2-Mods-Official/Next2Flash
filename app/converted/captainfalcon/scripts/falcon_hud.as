package
{
    import flash.display.MovieClip;

    public dynamic class falcon_hud extends MovieClip
    {

        public var carback:MovieClip;
        public var carwindow:MovieClip;
        public var p1:MovieClip;
        public var p2:MovieClip;
        public var p3:MovieClip;
        public var p4:MovieClip;
        public var scene:MovieClip;
        public var self:*;
        public var costumeData:*;
        public var camera:*;

        public function falcon_hud()
        {
            super();
            addFrameScript(0, this.frame1, 4, this.frame5, 76, this.frame77, 77, this.frame78, 127, this.frame128, 164, this.frame165, 171, this.frame172, 193, this.frame194, 198, this.frame199, 212, this.frame213);
        }

        public function updatePalette(_arg_1:*=null):*
        {
            if (this.costumeData && this.scene && this.scene)
            {
                SSF2Utils.replacePalette(this.scene, this.costumeData.paletteSwap);
            };
        }

        public function removeEvents(_arg_1:*=null):*
        {
            SSF2API.removeEventListener(SSF2Event.GAME_TICK_END, this.updatePalette);
        }

        internal function frame1():*
        {
            this.self = SSF2API.getCharacter(this);
            this.costumeData = new Object();
            if (SSF2API.isReady() && this.self)
            {
                this.costumeData = this.self.getPaletteSwapData();
                this.self.addEventListener(SSF2Event.STATE_CHANGE, this.removeEvents);
                SSF2API.addEventListener(SSF2Event.GAME_TICK_END, this.updatePalette);
                if (this.scene && this.scene)
                {
                    this.self.applyPalette(this.scene);
                };
            };
        }

        internal function frame5():*
        {
            this.camera = SSF2API.getCamera();
            this.camera.killDarkener(true);
            if (!this.self.getMetalStatus())
            {
                SSF2API.playSound("blueFalcon");
            };
        }

        internal function frame77():*
        {
            this.self.applyPalette(this.scene);
        }

        internal function frame78():*
        {
            SSF2API.playSound("blueFalcon_pass");
        }

        internal function frame128():*
        {
            SSF2API.playSound("FZeroStartupJingle");
            SSF2Utils.replacePalette(this.carwindow.carwindow, this.costumeData.paletteSwap);
            SSF2Utils.replacePalette(this.carback.falcon, this.costumeData.paletteSwap);
        }

        internal function frame165():*
        {
            SSF2API.playSound("yougotboostpower");
        }

        internal function frame172():*
        {
            SSF2API.playSound("impact");
        }

        internal function frame194():*
        {
            SSF2API.playSound("blueFalcon_pass");
        }

        internal function frame199():*
        {
            SSF2API.playSound("blueFalcon_leaves");
        }

        internal function frame213():*
        {
            stop();
            if (this.parent != null)
            {
                parent.removeChild(this);
            };
        }


    }
}

